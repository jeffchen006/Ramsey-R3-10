# Lane G experiment log

## Round 2: fixed residue at a degree-six root

- Read round 1 handoff, critic directives, core allocation (8), board, prior
  method and edge-table notes. The earlier degree-six proposal did not use
  the exact equality `e(G)=166` at the MTF private-neighbour floor. It is the
  smallest possible natural stratum with a degree-six vertex.
- The initial proof-producing SAT pilot retains all necessary MTF clauses,
  vertex degree/cardinality bounds, and optionally all independent-set cuts.
  At `e=166` the relaxation already suffices. Its positive calibration uses
  C35, saturated Exoo39, and 220 degree-six roots of the 10 pinned regular
  `(3,7,22)` graphs. `scratch/G/root/calib_relaxed.log` (3.88 CPU-s) and
  `calib_full.log` (53.09 CPU-s) record both calibrations. The latter is not
  required for the final proof or next round.
- The final core retains only independence and domination of each attachment,
  row cover, maximum-degree row caps, and H-nonedges needing an external
  common neighbour. Five necessary CNFs have 354 variables, 1,882–1,902
  clauses. No total-edge cardinality, lower degree bounds, PySAT, or alpha
  extension clauses. Every clause passes substitution of actual attachments
  on 294 smaller positive roots (`core_control.log`, 1.09 CPU-s); both
  exact checkers replay the five retained proofs (`replay_core118.log`,
  0.54 CPU-s). The independent column proof (`cover166.log`, 0.64 CPU-s
  with controls) gives a second reason for the 166 stratum in particular.
- The paper's 118-edge count is five. Exhaustive one-edge additions from
  those five yield 49 of the 69 `e=119` classes. Exact vertex-rewire + one
  edge swap closure of the resulting list finds no further class in
  15.83 CPU-s. A two-edge repair (after removals, add one edge in an
  uncovered independent-set witness, then require the second added edge
  to be in the intersection of all remaining witnesses) matches explicit
  exhaustive raw outputs on C5 (0 for 1→2, 5 for 2→2) and gives no extra
  class from the 54 seeds (4.30 CPU-s). These are negative experiments,
  not nonexistence proofs for the six missing classes.
- Deleting a vertex from the unique minimal order-34 graph (HoG file
  `Ramseygraphs_3_9_34_e129_some.g6`) or two vertices from C35 and then
  thinning edges gives four extra `e=119` classes. Exact rewire/edge-swap
  closure then gives ten more (20.14 CPU-s). This yields 5+63, or 68 input
  classes. Expanding the order-34 inputs by adding edges across levels
  130–135, extending vertex-rewire closure up to level 132 (19.47 CPU-s),
  and re-deleting/thinning did not improve the count. Thinning 865 generated
  `e=120` seeds (0.09 CPU-s), and rewiring a systematic 21-input sample
  (5.48 CPU-s; 29 lower-edge outputs), found no new `e=119` class. Files
  `scratch/G/root/{census119,thin_rewire119,catalogue119,from_sample120}.log`
  record timings/frontiers. All classes retained for proof use were then
  independently validated as triangle-free, alpha 8, and canonical-distinct.
- Both LRAT checkers confirm 68/68 necessary core contradictions on
  `root_certs/partial33_le119.g6` in 8.17 CPU-s (`replay_core119_clean.log`).
  This excludes these specific rooted inputs at every total `e`. The six
  uncovered isomorphism classes are the only catalogue blocker for extending
  the floor to 120, which alone would exclude another 55 distributions at
  `e=167`. No inference about those six from the measured probe.
- The class-LP pilot on the new floor uses a matched same-family solve at
  floor 118 whenever floor 119 produces an improvement. The venv wall
  timeout before a report is not evidence. System Python completed 20
  rows in 5.03 CPU-s with one improved bound; estimated 68 CPU-s for all
  269 eligible higher-edge cases at that rate, budgeted one process and
  capped it at 240 CPU-s/450 wall-s. Actual: 112.38 CPU-s, 61 improved
  bounds (sum of improvements 63 edges), all 63 certificates checked
  exactly as rationals. The one new closure conditional on gluing is
  `(8,0,2,30)` at e167. The same-family 118-floor baseline certified none
  of the 61 improvements at the target. Five cases cross to U88.

Raw per-formula logs and generated CNFs are under `scratch/G/root` (small
enough to keep for review). Only the five complete-cover proofs are shipped
as compressed binary files; the scratch paths are not needed for replay
of this claim without the optional Exoo controls. No detached G jobs were
started in this round.
