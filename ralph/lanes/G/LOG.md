# Lane G experiment log

## Round 5: complete degree-five obstruction, 85 independent cuts

- The old 65-core baseline (11.40 CPU-s) projects to about 23 CPU-h over
  the 477,142 order-27 cores. A maximal-independent-column filter cut the
  same pilot to 0.409 CPU-s; its eventual pass rate was only 118/477,142.
  All 32 production and audit shards cover exactly the round-robin source
  bytes and agree entry by entry. Both filters validate core alpha and
  triangle-freeness. The production and audit filters used 3,247.707 and
  1,396.751 CPU-s, respectively. Naive exact gluing ran only on 118 keys,
  not the full catalogue. Completeness uses the published exact count.
- The 118 survivors give no min-five order-33 extension at e<=122 (also
  118 dual-checked LRATs at cap122), exactly five classes first at e123,
  and 984 classes through the absolute cap130. Two exact enumerators
  produced 989 and 1,446 raw graphs with the same canonical output set.
  `audit_d5_cover.py --lrat .` checks final shard incidence, edge layers,
  validity, canonical set equality, and proof/verdict bytes.
- All 984 order-33 graphs fail d6-root full independence gluing, with
  zero survivors in two implementations (162.337 + 38.093 CPU-s). No
  total-edge, maximality or distribution assumptions in the gluer.
  Most higher e inputs were not suitable for a cascade of core LRATs:
  the eight-input pilot returned both SAT relaxations and wall caps.
  Only the complete, exact maximal-column search supports the global
  result (`enum`); the checkers do not turn that enumeration into LRAT.
- Hand bridge: at a d6 root, the exterior is `(3,9;33)`; it now has
  minimum degree at least six. Every nonadjacent pair in an MTF graph
  shares a neighbour. Two degree-six vertices therefore must be adjacent,
  and their class is a clique. Cuts 84 rows by unit Farkas sums. The one
  additional cut `(e,n6,n7,n8,n9)=(168,2,9,0,29)` follows from odd Z
  versus the required Z=48 (floor 120 and private bound). Five exact t9
  improvements. All 85 cuts and tightenings reconcile to round4_cases.csv;
  the two closed U88 rows are `(169,6,2,0,32)` and `(169,7,0,1,32)`.
- Exact smaller control: all 2,576 order-16 cores, both gluing codes
  recover all 178 minimum-degree-five order-22 classes and 70 canonical
  residue types from 944 roots; both outer predicates retain the 220
  roots in the ten regular order-22 controls. C13/C35/saturated Exoo39,
  all 191 saturated order-22 controls, and a 12-vertex positive with two
  adjacent degree-three universal roots test the degree/packing rows.
- Secondary d4 (order-32) triage only: 237/520 of the same order-27
  cores pass the relaxed gluing filter in 3.233 CPU-s. Not an exclusion;
  it would need an edge-capped or otherwise targeted stage before scale.
  No unchanged e120/e121 replacement sweep; the six missing keys stay
  open and the 11 old e169-pinned proof scopes are unchanged.
- On Lane B's pending degree-seven floor 108, a separate 90.58 CPU-s
  LP scan gives five additional exact cuts (two unglued, three using
  existing gluing floors) and 40 tighter threshold certificates on 39
  distinct keys. It includes the earlier e162 removal. Four U88 keys
  disappear and four are added; the count stays 10. Conditional baseline
  is 278+R; see `floor108_overlap.jsonl` and `floor108_summary.log`.

## Round 4: equality rigidity and a six-key census gap

- Before new work, froze the accepted round-3 cuts and U88 intersection with
  per-row witness locators. The degree-six equality case gives six allowable
  signatures from 3,700 labelled simple signature graphs (C13 positive at
  all 13 equality roots; C35 and MTF Exoo also pass). Exact rational Farkas
  replays: 6 independent exclusions with floors 120/107/95/86 and 13
  certificates under the threshold setting with floor 97. Integer pair
  packing excludes eight in 0.28 CPU-s, exactly matched on 2,450 small
  controls; the two additional exclusions have hand proofs and unit Farkas
  sums, using no floor but 120. All eight at e168. 368+R remain; U88=12.
- Witness edits: cache all independent (alpha+1)-sets created by one
  deleted edge. With two removals, any remaining violating set contains
  both removed edges; enumerate it by forcing their endpoints. With three,
  defer checking sets with >=2 punctures to the leaves, using the three
  forced endpoint pairs. For each uncovered set, branch on any legal
  insertion inside it, and forbid preceding alternatives. Exhaustive
  labelled equality on 60 small cells covering 1..3 removals and up to
  four insertions. Does not prove connectedness of the target class.
- Initial 2→3 at e120 and 2→2 at e121 gave 1,581 extra keys of the
  provisional e121 stream. Audit detected mixed levels: round 3's
  e120 stream had one e119; its e121 stream had 23 e120s. Strict split
  after iterative frontier gives 1,223/13,030. Earlier 5+69 e119 proof
  bundle is unrelated and unaffected. Boundary 121→122→121 with cached
  edits grew e121 to 13,076. Critical e122 / e123 returns gave 13,082
  then 13,087. Prototype 3→4 on 37 recent/critical sources gave five
  new classes relative to 13,082, overlapping three of the critical
  return; second pilot on 144 older critical sources yielded zero.
  Union 13,089. Full e122 lateral 2→2 (~0.45 CPU-h) produced just two
  extra e121s (13,091). Wide e123 bridge from 5,906 sources through
  230,936 new upper parents (~0.2 CPU-h) produced one more (13,092).
  Final rare frontier added no further keys. `scratch/G/round4/*.plan`
  and edit/canon logs record measured estimates and worker caps.
- Three vertices on 47 critical seeds gave zero new e120/e121 keys;
  square replacement also zero after exact seven-tag controls. Random
  add/thin excursions at depths 3/6/9/14 recover all three n8 controls
  but no new target classes in 8,000 walks. Naive degree-five gluing
  65 n27 seeds (11.75 CPU-s, no completion) would consume ~24 CPU-h
  over all 477,142 anchors; not scaled. For a d5 vertex in an order-33
  graph through 121 edges, its exterior H27 has >=85 edges and the
  neighbour degree sum is <=36. Private cells have <=4, so if U
  exterior vertices have no attachment then the sum is >=39−2U;
  at least two triangle-free incident additions are available. This
  is an observation, not a proof there are no degree-five cases.
- Exact supplied-root validity: pure independent alpha checks across
  baseline plus new deltas, strict levels and sparse canonical
  distinctness. 1,223 e120 inputs excluded unpinned. Of 13,092 e121
  inputs, 10,268 cliques and 2,813 unpinned dual LRATs cover all but
  11. Those 11 unpinned cores were SAT (not actual extensions); the
  e169-pinned degree/coverage relaxation refutes all 11 by both LRAT
  checkers. Total e<=168 cannot have a degree-six root with e121 by
  Z>=48. Unpinned full/triple-column samples hit caps and their
  sequential supervisors were stopped; no higher-scope result for the
  11. All pure one-edge children of the e120 catalogue occur
  in the frozen e121 list (12,289); all valid one-edge deletions of
  the latter give exactly the supplied e120 list. The 803 remaining
  supplied e121 classes are deletion-critical. The absent six types
  across both levels cannot be assumed to lie in either level. The
  count dependency is Angeltveit §§3.3 and 6 (14,395), not a claim
  the individual e120 count 1,223 was published as exact.

## Round 3: complete e119 cover, demand cliques and degree-seven floor

- Exact replacement fixes a labelled exterior after removing two or three
  marked vertices. Each added vertex needs an independent attachment hitting
  all exterior independent sets of size alpha; an internally nonadjacent
  pair needs its union to hit every exterior independent set of size
  alpha-1; three mutually nonadjacent additions require the analogous
  alpha-2 test. Internally adjacent pairs require disjoint attachments.
  Edge and degree bounds apply to the assembled graph. A branching
  independent transversal covers all solutions by choosing the first
  selected bit in an uncovered witness and banning earlier bits. Sorting
  masks and trying internal shapes covers all outputs modulo relabelling
  the marked vertices. Independent direct enumeration on the three n=8,
  alpha=3 controls gives exact set equality at 84 two-mark and 168
  three-mark exteriors (457 and 2028 raw outputs); every e118 original
  was recovered under each of its marks in the respective pilots.
- `joint119`: all 68 original e118/119 seeds, 6.26 CPU-s, found two new
  e119s. `basis120`: 865 old e120 seeds plus those two, 77.8 CPU-s, found
  one more. `grow120`: 71 combined e118/119 seeds gave 132 novel e120
  intermediates; `jointgrow` backward gives two further e119s. Triple
  pilot on the 5 e118s and 5 new e119s (28.86 CPU-s) yields the sixth.
  The union has exactly 74 verified classes across the two levels. Eight
  individual solve/check batches plus all-root replay are in
  `scratch/G/round3`; the retained full proof generation took 8.67 CPU-s,
  the no-solve hash/checker/Farkas replay 10.41 CPU-s. The published count
  is the completeness argument. A separate larger-seed deletion pilot
  recovered all 18 expected labelled C5 subgraphs on small controls but
  no target residue from 37 known larger order-38/39 source graphs.
- e120 follow-up: starting basis 997, 16 source triple pilot gave 94
  further classes (50.30 CPU-s); breadth 168 selected seeds, four shards,
  totals 1148 in roughly 480 CPU-s. The 1148 add to 10843 distinct e121s;
  spread 80-source pair return pilot adds four, 8.49 CPU-s. Full pair
  return through the 10843, six shards, yields 30 more to 1178, about
  1060 CPU-s. Demand cliques check 1125; both LRATs check all 53 exceptions
  in another 7.69 CPU-s. Count gap still at least 45. No proof of
  completeness/reduction of the next stratum is claimed.
- Degree 7: House of Graphs lists exactly 39 e104s, all verified. Direct
  old CNF pilot 8/8 then 39/39 LRAT certs, 3.79 and 19.58 CPU-s. The new
  clique test is more than two orders cheaper on that matched census:
  39/39 in 0.034 CPU-s plus trivial trace checks, then 951/952 in .80 s
  and 18531/18598 in 19.50 s. Both checkers verify all 68 complements; the
  consolidated independent replay is 44.49 CPU-s. Forged zero-bit demand
  rejects; C35 and saturated Exoo39 give 74 positive rooted controls.
  Initial full per-graph Python maximum-alpha recheck on e106 hit the
  140-second wall cap; the independently regenerated exact canonical
  addition equality plus inherited alpha replaces it (14.02 CPU-s).
- e107 feasibility only: 234341/234681 classes arise by addition. A
  60-source exact joint move scan from e106 adds 11 (10.53 CPU-s) leaving
  329 classes absent; 2925/2967 dispersed fixed roots have checked
  cliques (3.91 CPU-s generator). Do not count these as an e107 cover.
- Floor 120 LP full (213 cases, 68.51 CPU-s) and successive floors
  105/106/107 (334/326/320 cases, 52.83+58.44+59.92 CPU-s) produced
  169 rational certificates. Degrees 6 and 7 contributed 55 unconditional
  and 23 gluing-conditional incremental closures, respectively. Of 376
  near-regular open cases, 13 have a certified t9 upper bound 88.

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
