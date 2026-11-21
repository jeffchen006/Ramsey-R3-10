# Round 4: joining attachments on fixed induced cores

Allocation: two slots. The order-three I10=44 anchor was not searched again.
The new anchor is the degree-valid I10=142, 178-edge, order-40 attachment
from round 2. Its nauty form differs from the I10=44 graph (`anchor_compare.g6`).
The construction does not impose any permutation or invoke E's closed strata.
Unqualified data/log paths below are relative to `scratch/F/r4`.

## Coverage argument

Fix a valid triangle-free induced core H and let S_i be the neighborhood in H
of the ith new vertex. A legal column is independent in H, avoids old vertices
already at the degree ceiling, and hits every independent (k-1)-set of H.
For a pair of columns with intersecting S_i,S_j the poles cannot be adjacent.
The nonedge is allowed exactly when S_i union S_j hits every independent
(k-2)-set. A base vertex that would exceed the degree ceiling in those two
columns rules out both pair types. Enumerate unordered column tuples by a
nondecreasing ordering, intersect their compatible pair rows, then enumerate
the admissible triangle-free graphs on the poles. Repeated column masks are
allowed. A stable triple or quadruple of poles requires the corresponding
union of columns to hit every independent (k-3)- or (k-4)-set. These tests
classify all triangles and independent k-sets by their intersection with the
poles. Bitset layers enforce every old degree constraint, and each pattern is
checked for pole degrees and the total edge window. Up to relabeling the poles,
every feasible completion is covered. This generalizes the old two-vertex
rewire test; it does not infer any unpinned classification.

The first-uncovered-row recursion branches by the first selected available
member of the chosen constraint, removes earlier options in later branches,
and emits every compatible extension once when the constraints are all hit.
The compatibility join uses only queries on H: for fixed S_i, enumerate the
independent (k-2)-sets of H-S_i once, then test each candidate S_j against
those sets. Higher-arity constraints are evaluated only after filtering all
pair relations and degree multiplicities.

For an order-40 anchor, changing only edges incident with a set W of up to
poles vertices can yield a valid graph only if W meets every old independent
10-set. Pad W to the exact pole count, enumerate all such transversals, and
deduplicate the induced cores using `labelg`. The original marked transversals
are saved alongside every canonical row. The n39 sources instead project
every two-deletion core without a transversal filter. Scope is determined by
the actual finite input catalogue plus the degree/edge windows.

## Calibration and strict joins (enum unless noted)

- Independent CNF with all relevant triangle and independent-set clauses,
  sequential-counter degrees/edges, full model blocking modulo pole
  permutations: 38 small cores each for 2, 3, and 4 poles (`jsmall2exact`,
  `jsmall3exact`, `jsmall4tightexact`). The broader four-pole small oracle
  completed its first 21 rows, then hit CPU signal 24. Only the narrower
  completed control counts. The first two oracle invocations failed on a
  non-CSV terminal line and were rerun with a binding check.
- All three triple-pole C35 witnesses recovered, matching the SAT oracle and
  gate at 140 edges. On order 38: three triple-pole controls give 57
  completions; seven four-pole controls, covering all triangle-free internal
  types, give 52 at e=165. All planted witnesses are recovered. SAT agrees
  exactly and both gate algorithms pass every completion (`jctl*exact`,
  `jctl35.gate`, `jctl38gate.stdout`, `jctl38quadgate.stdout`).
- Anchor transversals: 748 distinct order-37 cores and 9,490 distinct
  order-36 cores. Full completion in degree 4..9 and e=161..180 found zero
  on either (`janchor37full`, `janchor36full`), closing only those edits of
  that anchor. The three-pole run found zero compatible tuples after testing
  5,881 columns and 2,159 pair links. **estimate:** on the same 48 spaced
  order-37 cores, C++ 0.04 vs independent Python/CaDiCaL 28.76 CPU seconds
  end-to-end; full C++ 0.72 CPU seconds for 748, and 14.72 for 9,490.
- Three structurally valid nonisomorphic order-39 inputs (Exoo, one round-1
  random construction, one round-2 exchange output) give 2,223 marked and
  2,221 canonical order-37 cores. Zero three-pole exact completions
  (`jsourceprep`, `jseeds37full`, 4.47 CPU seconds). Scope is induced cores
  of these three inputs, not all order-37 graphs or any symmetry class.

## Nearness objectives

**One imperfect pole.** Enumerate clean triples on the 9,490 anchor
cores, then optimize one final attachment to each valid order-39 graph.
The final degree window is 4..9 and e>=161. `attach_score.cpp` now includes
the total-edge floor as an additional minimum degree requirement for the
last pole; it cross-checks optimal scores by exhausting all eligible
independent subsets. C35 and order-38 positives pass the gate, with a
C35 e>=141 negative. The 43,387 labeled clean triples yield 672 canonical
order-39 graphs, of which five are outside the exact 28,113-class round-2
component; optimum I10 stays 142 (`janchor36scorefull`, `scorefull.*`,
`jscorefull`). The clean pair join on the three order-39 seeds' 2,221 cores
initially hit output caps on two rows. Replaying just those rows without
caps in the completed domain yields 33,533 total labeled completions after
replacement, 17,275 canonical graphs, 17,073 outside the round-2 component.
No claim about their membership in Exoo's or the historical components.
Verified exhaustive attachment optimum on this 17,275-graph pool is I10=134
(48.03 CPU seconds, 17,273 feasible); three exhibited optima are independently
recounted, with e=176 or 177. See `jseeds37pairfull`, `jpairrescan`,
`seeds39pairs*`, `jscoreseedsfull`, `seedbest134.audit.jsonl`.

**Two imperfect poles.** For a valid H and independent columns A,B, the
score is I_(k-1)(H-A) + I_(k-1)(H-B), plus I_(k-2)(H-(A union B)) if the
poles are nonadjacent. Each term counts bad sets with a prescribed
intersection with the poles. Enumerate all independent column masks whose
first-term count meets the supplied ceiling. Equal projections of old
(k-1)-sets carry multiplicities. Score-sorted pairs prune only by a lower
bound, and if the adjacent mode is feasible it cannot score worse than
the nonadjacent mode. Otherwise the nonadjacent term is counted exactly up
to the incumbent cutoff. One minimum witness per core, not all tied minima;
`NA` means no extension within the score ceiling. A census at ceiling T
excludes only the searched cores within the declared degree/edge bounds.

Controls: 38 exact small brute-force checks, plus forced C5 constructions
with scores 10 (adjacent), 15 (nonadjacent), and a tight-ceiling negative at 14.
Both order-38 controls returned zero and passed both gate algorithms
(`jsoftsmallaudit`, `jsoft{adj,nonadj,cap}.stdout`, `jsoft38.gate`). The full
39 transversals of size two on the I10=142 anchor give four score<=141
witnesses, three canonical; the minimum I10=122 has e178 and degree 8..9
(`anchor38score.audit`, `pairbest40.audit.jsonl`).

## Two-pole improvement and follow-up

- Projecting all one-vertex deletions from the 672 anchor-derived order-39
  graphs and the 64 best-scoring outside-component graphs of the clean
  pair pool gives 28,704 marked and 25,019 distinct order-38 cores. The
  256-row timing sample took 0.86 CPU seconds and scored 100. The exact
  ceiling-121 pass took 81.06 CPU seconds and had 134 emitted optima, all
  checked by independent recount and exact row/index reconciliation.
  Minimum I10=26 at row 5255, e178, degree 8..9 and trivial automorphism
  group. Its 26 bad sets split 12/14 by single-pole membership; no vertex
  belongs to all of them (`jproject38*`, `projectbest26.*`).
- All four-vertex repairs of this new anchor were checked at the same
  degree/edge bounds: 7,249 marked transversals reduce to 7,191 distinct
  cores, zero strict completions, no caps, 21.33 CPU seconds
  (`jbest26w4prep`, `jbest26strictfull`). This closes only that induced-core
  neighborhood. The strict four-pole check says nothing about a change
  touching the union of five or more vertices.
- A dispersed **256-window subset** of the 7,191 cores gave 12,342 labeled
  clean two-pole completions to order 38. These reduce to 10,700 canonical
  cores, 10,655 not in the previous 25,019-core list. Soft two-pole
  addition, ceiling 25, gives exactly three emitted minima of 24 across
  those 10,655 cores in 18.96 CPU seconds; the other rows have no completion
  within the ceiling. This is not a sweep of all 7,191 cores in the soft
  mode. Recount independently confirms all three witnesses. Two canonical
  order-40 graphs remain, with 178 and 179 edges, degree 8..9. Both have
  automorphism group of order two with zero fixed points. `countg` and
  a separate pynauty cycle-type report agree (`best24.symmetry.log`,
  `best24.pynauty.log`). The gate rejects both for independent 10-sets.
  The durable seeds are `round4_seed40_24.g6` (178 edges) and
  `round4_seed40_24_e179.g6`. No graph went to `ralph/found/`.

The 24s improve Lane F's degree-valid order-40 score from 44 overall and
from 108 in the free-involution family. The historical one-pole value 23
in `notes/known39.md` is not part of this run and has no local graph file.
Do not promote a near miss or any local enumeration to a Ramsey verdict.

## Replay

Compile `pole_join.cpp` and `attach_score.cpp` with
`g++ -std=c++20 -O3 -Wall -Wextra -Werror` into `scratch/F/build`. The
last binary in this round is `pole_join4soft` (strict mode omits the optional
score ceiling). `pole_audit.py` regenerates control cores and marks, exhausts
the independent SAT/brute controls, and independently recounts soft outputs.
Exact commands, supervisors, resource limits and timings are recorded in
the round-4 jobs table in `STATE.md`. All timing estimates for scale-ups are
in the corresponding `*_cost.txt`; each output family is keyed by the
zero-based row of its explicitly named input. Canonicalization is always
`opt/bin/labelg -q`, then `LC_ALL=C sort -u` where deduplicating. Neither
enumeration nor recounts are certificate proofs. No numerical near miss is
eligible for `ralph/found/`.
