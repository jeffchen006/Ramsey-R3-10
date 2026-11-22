# H — round 23 review (November 22, 2026)

## Ledger import

`ralph/critic/round_022.md` supersedes the partial E-048 and F-040
rows and confirms the 149 m15 replays, 539 same-pole m14 keys, and 49
h6 boards at their own levels. The five m14 prefix-covered parents are
inside the 539. The 211-board h5 checkpoint is inside 224, leaving 62
at that cutoff. Separate negative entries preserve the original rejected
2,686-key D mixed tally and the reversed G replay reader without using
either as a refutation or invalidating the checked cover. No referee-022
artifact or scout submission to import. Counts and premises are explicit
in `ralph/CLAIMS.md`.

## H-039: guarded physical witness clauses (Lean, pending)

The row in `lean/R310/SelectedWitness.lean` lists one negative literal per
needed pair selector and one positive variable per represented pair. On
the guard-true branch the coordinates must name distinct physical sites
and the pair list must cover each unordered pair. A physical edge must
have a true positive literal; this includes proving nonadjacency of a
pair represented by no literal, whether a root/anchor/contact nonedge or
triangle obstruction. Otherwise, falsifying the row makes the injective
image independent of size at least `bound`, contradicting the graph's
independence number. At ten this applies to the exact G row, *including*
the listed physical boundary sites, not a heuristic short padded row.
Neither the implementation producing the row nor the extraction of all of
those premises from every board model is a Lean theorem here. In
particular there is no SAT-to-graph converse.

The full/compact equivalence is separate: if all selectors are true,
any omitted bit must be false. A shared physical contact and projection
direction prove it in a graph. Alternatively a satisfied base channel
clause `¬g₁ ∨ … ∨ ¬gⱼ ∨ ¬edge`, whose local selectors occur in the
outer row, suffices directly on a Boolean assignment. It does not permit
dropping a guard or a genuinely free edge.

### Calibration and replay

- C13(1,5): `α=4`, all 39 independent fours, all 1,287 five-sets, four
  guard patterns each, 8,580 false edge occurrences omitted. Removing
  the sole true edge makes 78 valid selected five-set rows fail.
- All three frozen A width-three plants have `α=6` independently. The
  short-witness, dropped option edge and dropped selected guard mutations
  each fail the intended control. The guard fixture uses counterfactual
  witness coordinates rather than plant graph6 vertex numbers.
- `check_selected_witness.py` compares exactly four smaller-in-scope
  **target relaxation** I10 rows against the two published model graph6
  records, all 180 physical unordered pairs and 87,000 base CNF clauses.
  The 21 deleted positive literal occurrences all cite actual satisfied
  channel clauses in the frozen base CNF with only outer selector guards.
  Both full and compact rows falsify the respective model. This is a
  four-row executable binding audit, not general checking of target rows.
- Cached Lean/Mathlib 4.35.0 `--old build R310` passed. Targeted and full
  strict scans contain 5 and 374 axiom reports with only the standard
  permitted axioms. Full query retry with `lean -j 1` passed after a
  transient thread creation fault; the failed attempt earned no reports.
  Logs: `scratch/H/round23-{dev,dev2,build,axioms-targeted,axioms-project,axioms-project-retry,strict,controls,toolchain}.log`.

From the workspace root (one CPU per command):

```bash
bash ralph/lanes/H/build_private_signature.sh --old build R310
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 ../ralph/lanes/H/SelectedWitnessAxioms.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j 1 scripts/Axioms.lean
python3 -BS ralph/lanes/H/check_selected_witness.py scratch/A/r23
```
