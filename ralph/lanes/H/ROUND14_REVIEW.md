# H round 14 — ledger and formal interfaces

## Round 13 review imported

`ralph/CLAIMS.md` now applies `ralph/critic/round_013.md`, including the
late D, E, F and G decisions. The accepted near-regular ledger is still
**238 plus R** (ten conditional U88 keys). G-042 rules out 12 *universal*
degree-nine residue floors one edge higher than the revised cutoffs;
it provides a small-residue witness requirement on **some** d9 root,
not an assertion about every d9 root, and no new profile debit.

* **D:** existential double bouquet, 101 sufficient rooted candidates,
  528 unordered internal type pairs. Mark 179 is replaceable, not
  forbidden; five C8/C8 labelled boundaries do not eliminate that pair
  of types. No product of these counts is asserted to count cases.
* **E:** only mixed core 17 under E-021 and the stated conditions, seven
  remain. **0.62728 core-h** is terminal work including the second
  Python audit, not whole round. The separate 98-wrapper sum includes
  pilots and is already **0.67977 core-h**. The matched three-band
  3,530→1,508 CPU-s price is not end-to-end measured closure time.
* **F:** five necessary cyclic inter-pair words, no realizations or
  unrestricted automorphism closure. The crossing-degree hand result
  does not assume cyclicity. The 693 column inputs are not quartets.
* **B:** retain the separate denominators **14,395** for the complete
  33-through-e121 census and **2,104,146/2,104,151** for the supplied
  32/e108 catalog. Both the missing keys and a covered reducible
  extension obstruction are required for a floor 109 argument.

## Lean interfaces and physical calibration

* `R310.PoleContacts`: on the actual induced old card, use the graph
  isomorphism only on old edges. If the image of the independent pole
  contact set avoided that pole, adding the pole contradicts the
  independence cap. Fixed-point-freeness prevents a singleton orbit
  from qualifying; for an involution the found contacts form a full
  2-cycle. Separately, three other poles in a triangle-free graph
  include a nonedge; both its ends can be added to a disjoint column.
  At most one free slot per old site ensures pairwise column
  disjointness, specializing to old minimum degree eight and α≤9.
  This does not count holes or prove the full crossing-degree bound.
* `R310.BookFootprint`: induct over a finite family. Adding a set loses
  at most the sum of its intersections with the preceding sets. Count
  ordered off-diagonal intersections and double the other terms, so
  no natural-subtraction artifact. The graph bridge gives exact demand
  from degree minus internal degree, and bounds external overlaps by
  stated codegree caps minus internal overlaps. An 11-site book leaves
  29 outside sites; for two disjoint books only 18 are off both, giving
  the opposite-contact inequality. No 41-type list, proof farm, CNF
  or R(3) reroot premise imported.
* `check_round14_controls.py`: C5 positive, one-contact deletion to
  P5, all 388/5,789 labelled triangle-free graphs at orders 5/6,
  333 maximum-contact mates, 9,171 disjoint images extending by the
  pole, 1,886 physical disjoint-column arrangements (1,308 nonempty
  tight columns) and 3,903 overlapping negatives. 416 and 7,040
  physical degree/overlap footprints on C13 and the ten regular C22
  hosts respectively, including 5,260 counterexamples to omitting the
  overlap debit. The first P5 witness used a wrong mask; replaced by
  the literal `{0,2,4}` and reran the complete controls.
* Reproduction on the pinned cache: run
  `bash ralph/lanes/H/build_private_signature.sh build --old R310`,
  then `env lean ../ralph/lanes/H/AxiomsRound14.lean` via the same
  wrapper, and `python3 -SB ralph/lanes/H/check_axioms.py` on the
  Lean script and its log. No Mathlib source build, no H solver jobs.
  Eight targeted and 327 integrated axiom reports pass with only
  `propext`, `Classical.choice`, `Quot.sound`. The initial integrated
  process failed to allocate a thread (exit 134); an explicit
  `env lean -j 1 -DElab.async=false scripts/Axioms.lean` retry passed.
  The measured Lean cost including development and failed invocations
  was 219.88 CPU-s; physical controls used 0.86 CPU-s.

## Current-round receipts

A's independently packed first-shard roster and bounded depth replay
match C's frozen producer digest. All 785 panel IDs bind two terminal
vectors; 174 joint, 3,086 fillings, zero open on `[0,2048)`. It is a
complete **shard** of one marked cap-five block, not of Case R. A's
final receipt binds the **12-shard prefix** through left frame 24,575:
67,417,211 ordered headers, 12,594 matched vectors, 3,464 joint IDs and
148,231 rejected fillings. C stopped after the already resolved
`23155/26938/1` took 3.859940 CPU-s for 7,059 I10 dispositions; this
exceeded the one-second pricing gate, not a logical timeout. The
90,054,790-header complement is not covered. Prefer pricing work on
this actual tail and independently binding any new terminal checker
before funding the remaining intervals.
B's submitted 32,768-key named reducible tranche is independently
useful even while five inventory keys are missing, but awaits critic
and leaves the rest of the named extension list. No floor 109 or
U88 change follows.
E's mixed core 5 and F's cyclic word 15 are submitted, not accepted
counts. Ask the critic to rebind the exact E premise and F signing
cover separately; they do not alter the overall Ramsey split.
