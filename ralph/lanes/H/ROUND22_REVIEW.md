# Lane H round 22: folded physical slot semantics

## H-037 — Lean, with enum controls; pending critic

`lean/R310/FoldedSlot.lean` isolates the edge identification used by
N-010 and relevant to the two-defect extension. It has no enumerator,
no solver, and no SAT byte binder.

- A selected pair names one physical vertex. A left slot and a right
  slot each have at most one selected mate. Physical placement is
  injective on active left slots and agrees across each selected pair.
  Right-side injectivity and distinct vertices for any two distinct
  selected pairs follow. No condition on the injectivity of support
  masks is imposed.
- `foldedGridEdge_iff_adj` takes actual contact membership (inclusion
  suffices). If a physical edge exists, the masks cannot share an
  anchor, by triangle-freeness. Thus after activation a folded edge
  literal is equivalent to the actual edge, including when a mask
  overlap forces one shore's literal to be false.
- `guarded_folded_grid_edge` identifies the two shores' descriptions
  of the edge from a selected site to the same physical grid copy.
  `guarded_folded_slot_edge` uses two selection guards for two such
  sites. Neither conclusion equates descriptions under an unselected
  option. Inactive slots have false literals by definition.

The scope is the **necessary** truth assignment induced by a physical
placement. The theorem does not derive the equality populations,
construct the finite labels, bind their activity/cardinality incidence,
prove the grid or slot lists exhaust the graph, bind MTF or padding
clauses, or check any target CNF or LRAT. It is not a new case closure.

## Reproduction and controls

```bash
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean ../ralph/lanes/H/AxiomsRound22.lean
bash ralph/lanes/H/build_private_signature.sh env lean scripts/Axioms.lean
python3 -SB ralph/lanes/H/check_folded_slot.py
```

The Python controls verify triangle-freeness and independence number
four for `C13(1,5)`. On 52 oriented adjacent marks they check 312
selected grid-edge descriptions, of which 104 are true and 104 clash
on exactly one shore; 624 unselected descriptions actually differ.
The equal-mask fixture has two distinct optional sites with identical
left **and** right supports, and two distinct grid copies with identical
cell labels. Their adjacency rows are `(1,0,0)` and `(0,1,0)`; identifying
the optional sites or the copies by mask loses a valid physical graph.
All 24 name permutations pass. A third grid copy forces a constant false
on the left only. The reused-left and reused-right gate mutations fail
the matching predicate. A second fixture checks 36 labelled placements
of three optional sites with one true edge and two left-only clashes.
Neither fixture is presented as a target equality graph.

Lean/Mathlib v4.35.0; final build succeeds. The strict checker reports
5 targeted and 367 first-pass project axiom reports, with only standard axioms;
the two distinctness/injectivity results depend on none. An earlier
aggregate attempt failed to create a thread; only the clean final sweep
counts. Timed development, builds, axiom sweeps, version and controls
used **178.00 CPU-s = 0.04944 core-h**, peak **3,449,108 KiB** RSS. Logs:
`scratch/H/round22-{build-final,axioms-targeted-final,axioms-project-final,strict-final,controls-final,toolchain}.log`.

## H-038 — C-050's physical degree count (Lean, pending critic)

`lean/R310/CardDegreeBudget.lean` is the finite counting step only.
For an actual neighbour set `A`, prescribed set `P⊆A`, and disjoint
physical groups `S_i`, the terms `(A\P)∩S_i` are disjoint in `A\P`.
Cardinality of the disjoint union bounds the sum of the separate
lower bounds by `|A|−|P|`. The graph wrapper takes `A=N(site)`.
No minimizer choices, equality of local isomorphism types, or common
minimizing restoration are assumed. Proof of the lower bounds and
exhaustiveness of the local domains remain on the card side. This
does not revisit C's negative target gate or its signed join.

`check_card_degree_budget.py` checks 3,328 physical allocations on
`C13(1,5)` (1,053 tight) and compares all per-allocation feasible two
lower bounds. Reusing the same new neighbour in both groups or
counting the prescribed edges again falsifies the proposed bound
on a degree-four control with one additional incidence available.
Final combined cached build and strict **2 new targeted, 369 project**
axiom reports pass. This pass adds **74.58 CPU-s** (0.02072 core-h),
for **252.58 CPU-s / 0.07016 core-h** of timed Lean and controls overall.
Logs: `scratch/H/round22-{budget-controls,budget-axioms,combined-build,combined-axioms,combined-strict}.log`.

## Scoped imports

The round-021 critic decisions update all twelve pending lane rows.
N-010/011, R-007/008 and N-012/013 record the accepted scout coverage,
conditional proofs, and separate prices/source pilots. In particular
51→235→1,213 `h=7` keys, 565,384+32+115 for conditional core 1, 159→150→149
marked R(3) supports, and puncture-subgraph floor 97 over host floor 108
are four different denominators. No round-21 T or referee artifact.

Round-22 lane claims imported as pending only. In D's provisional
handoff, a metadata join (not another proof replay) matches 149
distinct host IDs in the manifest with 149 lane replay records; all
extract/rebind and two-checker steps report success. The manifest
weights sum to 427,324 ordered pairs and 250,440 marked orbits.
