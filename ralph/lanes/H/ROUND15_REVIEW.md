# Lane H round 15 — ledger binding and biclique window implication

Confirmed statuses in the ledger are from `ralph/critic/round_014.md`.
The accepted global balance stays at 238 near-regular distributions
plus Case R, with ten conditional U88 keys. Conditional mixed core 5
closed, leaving 1, 6, 8, 9, 15, 18; the new submission for 8 is pending.
The order-32/e108 census lacks five keys even if the reducible campaign
closes every supplied residue. The 36,800 distinct reductions include
the earlier pilot, with 64 overlaps in the 32,768-key round-14 tranche.

## Imported rounds and scope

- A-024/025 and C-038: roster and directly checked prefix, not the full
  block in round 14. Reason agreement is by alignment as a count vector,
  not a keyed equality of reasons on individual fillings.
- D-035/036: **every** deficient path in R(3) has at least 13 induced
  pentagon closures; **some** deficient path has at least 16. The second
  mark need not occur in a preselected pair of marks. Nine original local
  CNFs were dual checked (five and four); D-037 reuses the four triad
  checks. No global LRAT, matching of 13/16, or general ban on an
  all-deficient pentagon. D-038–040 distinguish rooted counts and
  structural cuts from a sampled experiment without whole-root cuts.
- F-025–027: IDs 15, 43, 81 excluded; 43 and 81 force at least 36
  distinct independent tens on the old card itself, for every vertical
  choice. The two remaining cyclic words (8,21) are not realizations.
- G-045–047: both edge tables free but populations fixed in the three
  exact contradictions. The fourth witness fails triangle and window
  constraints, and the free-template caps are not whole-template cuts.
- H-028/029 and E-036/037 accepted as scoped. New producer submissions
  are tagged pending, not treated as ledger debits. A's and C's full
  receipt totals independently agree: 92,341,930 direct, 65,130,071 via
  shore exchange, 0 uncovered. This is the best currently measured
  regular route for a bounded subcase, not a route proven to cover all R.

## Lean and smaller controls

`lean/R310/BicliqueNeutral.lean` proves the union cardinality and bound
using triangle-freeness and complete cross adjacency; the two nonempty
independent four-sets must be disjoint by irreflexivity. For either
induced root window, a maximum independent set adjoins all four roots.
Thus its independence number is at most five, and the explicit
`Ramsey3Le 6 18` hypothesis bounds the window by 17. Inclusion-exclusion
uses the literal common antineighborhood of the two shores. The theorem
does not use 9-regularity or a codegree cap; those hypotheses are for
the subsequent frame coverage. It certifies no catalogue, rejection,
scanner, exchange transport, or absence of marked graphs.

Run the pinned build without rebuilding Mathlib:

```sh
bash ralph/lanes/H/build_private_signature.sh --old build R310
(cd lean && bash ../ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false ../ralph/lanes/H/AxiomsRound15.lean)
(cd lean && bash ../ralph/lanes/H/build_private_signature.sh env lean -j 1 -DElab.async=false scripts/Axioms.lean)
python3 -SB ralph/lanes/H/check_biclique_neutral.py
```

Five targeted and 332 integrated axiom outputs pass the existing strict
checker. The control independently verifies the known smaller Ramsey
threshold (12 labelled order-5 graphs and zero order-6 graphs with
α≤2); then 1,494 order-7 triangle-free α≤4 planted squares pass the
window identities. The tight `C4 ⊔ C5`, a one-contact asymmetric
variant and a mixed-contact triangle mutation distinguish the premises.
These controls reuse no scan frames. Build and checks, including the
first failed elaboration at the local `let` rewrite, measured 114.78 CPU-s
total (0.03188 core-h). No lane-H solver process.
