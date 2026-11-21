# Round 5: disjoint core pools from the two score-24 seeds

Allocation: four slots. Seed A is `round4_seed40_24.g6` (178 edges),
seed B is `round4_seed40_24_e179.g6` (179 edges). The n40 searches require
triangle-freeness, degrees 4..9 and 161..180 edges. No permutation is imposed;
the source graphs have fixed-point-free involutions, but the searches are
not an enumeration of any involution case. Data paths below are relative to
`scratch/F/r5`. The exact commands and resource bounds are in `STATE.md`.

## Scoring identity and pruning (hand)

Fix an induced core H and add p poles with core neighborhoods S_i. The score
of the result is the sum, over independent pole subsets U, of the numbers
of independent (k-|U|)-sets in H outside the union of S_i for i in U.
Indeed every independent k-set induces just one such U and a disjoint core
part. The term for U empty is the fixed score I_k(H). A core with fixed
score higher than the target can never improve it; otherwise subtract that
term from the available budget. This lets a sub-24 search retain existing
bad sets, not just repair transversals covering all of them.

For three poles, enumerate columns ordered by singleton charge, check the
old degrees via at-least-load layers, then check every legal internal pole
pattern. Disjoint columns are necessary for an internal edge. Cache each
missed-set count for a nonedge pair within its tuple. If counting stopped
at the remaining budget, the truncated count remains sufficient to prune
any later pattern that needs the count (the incumbent cannot increase).
Only the edgeless pole pattern pays the triple charge.

For four poles, carry the feasible labeled triangle-free patterns in a
bitset. On appending a column, charge every newly determined stable
subset to all patterns that require it. Each count can stop at the
threshold for the pattern with the smallest subtotal among those charged;
if that threshold is reached, all charged patterns are already infeasible.
The minimum future singleton charge is the last selected column's charge
times the number of remaining poles. No negative terms are used. An edge
floor, old-neighbor load and complete pole degree filter are applied only
where their bounds are valid. Repeated columns are allowed. A score row
emits one optimal witness, not all ties. The numeric per-core output cap
in the CLI applies to strict enumeration, not to the soft optimizer.

## Calibrations (enum)

- Matched order 38: old strict triple search equals independent SAT on
  all three cores (57 completions) and recovers every planted completion;
  the soft pair/triple/four modes return score zero on 2/3/7 respective
  cores, and every returned witness passes both gate algorithms. The
  strict four-pole replay also gates all 52 completions.
- Independent whole-graph small brute force agrees on 76 triple scores,
  76 four-pole scores, and another 114 with the fixed-score mode enabled
  (38 each for two, three and four poles). The `qctlcombo` wrapper's first
  attempt lost the terminal line on stderr; all calibration claims refer
  to `qctlcombo2` and the successful `fixedCtl` run.
- The faster graph6 deletion encoder matched the previous relabel/encode
  pipeline on 1,536 deterministic deletions of sizes 2, 3, and 4. Its
  order-36 non-clean generation finished after the old Python encoder's
  CPU-cap exit (`prepFixed`, `prepFixed4Fast`). This is an engineering
  measurement, not a classification.

## Exact input scope

`disjoint_cores.py split` marks every deletion satisfying the fixed-score
condition and canonicalizes the core with `labelg`. A graph shared by the
two parents goes to A, with both provenance lists retained. A prior key
is dropped only by exact canonical equality against explicitly named
catalogues. `del2`, `del3`, `del4` use fixed score zero. `fixed2` through
`fixed4` use fixed score 1..23. Pool lengths and digests are in `prep*`.
The zero-score scope is all permutations of the appended poles; these
searches do not freeze replacement pole labels relative to the seeds.

The clean order-38 promotion joins two clean poles against `del4.A` and
`del4.B` (2,801 and 3,458 new order-36 cores). For a possible n40 target,
the promoted core has minimum degree at least 2, maximum 9, no independent
10-set, and at least 143 edges since the two final poles contribute at
most 18 edges. The per-core initial cap of 8,192 emitted completions
truncated seven B rows. Their replacements independently reconcile the
original row index and internal-edge counts, and all seven replays
complete (largest 119,878). `recover38` reconciles 33,392 A and 674,930 B
labeled completions (after replacement), verifies each core prefix before
canonicalization and leaves 15,519 A and 470,693 B previously unseen
canonical order-38 cores after subtraction of the prior order-38 lists
and current direct `del2` scans. These counts describe only the finite
catalogue, not all inducible cores of either seed or all n38 cores.

## Results

| Label | Search | Outcome | Evidence in `scratch/F/r5` |
|---|---|---|---|
| enum | 486,212 unseen canonical order-38 promoted cores; exact two-pole score ceiling 23 | Zero qualifying outputs, no cap; 739.66 CPU seconds for the three production blocks | `s38full{A,Bpart0,Bpart1}.{stdout,tsv,time}`, `auditProm38.stdout` |
| enum | Strict four-pole repairs of the two score-24 seeds | 6,259 new and 936 previously exhausted canonical order-36 cores, no completions; union binds all 7,195 distinct clean four-deletion cores from both seeds | `strict4full{A,B}.*`, `auditStrict4.stdout`, `auditBothSeeds.stdout`, previous `scratch/F/r4/j{anchor36full,best26strictfull}.stdout` |
| enum | Exact soft repairs on unseen clean cores | No score below 24 on 3 two-deletion, 280 three-deletion, or 6,259 four-deletion cores. Every emitted score-24 witness (2,801 A, 1,937 B) was independently recounted and canonicalizes to its respective input seed | `qfull{A,B}.summary`, `auditQ_A.stdout`, `auditQ_Bprefix.stdout`, `qB_*.stdout`, `auditFinal.stdout` |
| enum/open | Non-clean repair allowing fixed bad sets | No score below 24 on all 742 two-deletion and all 8,866 three-deletion cores with fixed score 1..23. Four-pole pilot: zero improvements on 768 of 75,578 cores; remainder not searched | `prepFixed*.stdout`, `fixedfull{2,3}{A,B}.summary`, `auditFixed23.stdout`, `fixedpilot4{A,B}.summary`, `auditFinal.stdout` |

Any n40 completion by editing only edges incident to at most four vertices
of either seed can be covered by padding those vertices to four. If the
unchanged induced core contains a bad set, that completion is impossible.
Otherwise the core is in the strict 7,195-key union. This is an enum result
for two local neighborhoods, not a symmetry-family exclusion or a claim
about all possible n40 graphs. The soft four-pole result covers only the
6,259 new keys; prior strict checks do not imply a prior soft lower bound.

The initial soft-B run at ceiling 24 received CPU signal 24 after 1,937
finished rows. `qfullB.prefix.summary` appends a terminal line only for the
verified prefix; the original nonterminal log is retained. The isolated
interrupted row and two disjoint 760-row suffix shards all completed at
ceiling 23 (24.90, 30.43, and 40.41 CPU seconds). Concatenating the prefix
and shards exactly reproduces the input catalogue. No claim of plateau
enumeration is made for the suffix, and even the 24-scored rows return only
one witness per row. The finite soft lower bound is unaffected by using a
lower ceiling on the retries.

Round total: 55 registered jobs, 1,393.94 CPU seconds (0.3872 core-hours),
peak four slots, no live jobs or candidates. Degree-valid best remains
I10=24, with no new canonical seed. Avoid rerunning the exhausted pools;
the non-clean four-pole tail is estimated at about 17 CPU minutes before
outliers and had no gain in its dispersed pilot. No request for more cores
or memory. A genuinely different parent pool or an improved selector would
justify another calibration; a larger unchanged local sweep is not the
default next move.
