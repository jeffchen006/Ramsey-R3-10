# Lane H, round 12 — November 22, 2026

## Lean and calibration

- `DeficientWitness.lean`: a marked pair is a nonedge with distinct
  ends, adjacency to the named common neighbour, and uniqueness.
  Hitting both disjoint same-colour pairs puts both ends in the shared
  neighbour's set. Uniqueness then contradicts the new colour. The
  root-choice theorem assumes the initial disjoint pair of pairs and
  a different colour from the first. Neither premise is imported from
  enumeration; the conclusion is disjoint **endpoints**, not paths.
- `ReciprocalWindow.lean`: three applications of the two-set cardinal
  identity give the triple closed-neighbourhood formula. At order 40,
  degree nine on the independent roots, a completely joined opposite
  triple and cap-five codegrees, this proves `|F| = 10+p−h ≤ 22` and
  characterizes equality. A supplied `|F|≤20` plus three codegrees five
  gives `|F|=20,h=5`. The bound `≤20` opposite `22` remains dependent
  on C-031/C-033; it is not proved by Lean here.

The physical controls on the known McKay order 13/17/22 lists verify
312 / 6,146 / 446,612 distinct-colour comparisons against disjoint
same-colour marks, and 78 / 1,561 / 109,845 independent triple counts.
C5 has five endpoint-disjoint and zero path-disjoint two-colour marks.
Planted same-colour pairs verify the bridge; overlap and extra common
neighbour mutations exercise its premises. Four local 40-vertex
fixtures realize window orders 22, 20, 21, 21, including both forbidden
21 profiles of the reciprocal problem **without the reciprocal global
premises**. They are count controls, not Ramsey candidates.

Using the existing Mathlib v4.35.0 cache (no source build):

```bash
bash ralph/lanes/H/build_private_signature.sh build --old R310
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 ../ralph/lanes/H/AxiomsRound12.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 scripts/Axioms.lean
python3 -SB ralph/lanes/H/check_axioms.py ralph/lanes/H/AxiomsRound12.lean scratch/H/round12-targeted.log
python3 -SB ralph/lanes/H/check_axioms.py lean/scripts/Axioms.lean scratch/H/round12-project.log
python3 -SB ralph/lanes/H/check_round12_controls.py
```

Build and all 4 targeted / 310 integrated reports succeed, with only
`propext`, `Classical.choice`, `Quot.sound`. Evidence is in
`scratch/H/round12-{build,targeted,project,controls}.log`.

## B dependency chain for the in-depth audit

`check_round12_b.py` binds B's exact 33 terminal shards, their d7/d8
raw counts and ordered-key hashes. Their disjoint inputs match all
7,954 prescribed fresh parents, distinct from the earlier 471 and
745 queues; all 1,724 output keys occur in the existing critical set.
It does not replay lifting semantics, canonicalization, proof semantics
or producer searches. It also streamed the ordered union of the actual
frozen 2,102,271 reducible and 1,875 critical files and rechecked the
47-key delta and 37+10 B-027 receipt identities.

The count is still 2,104,146. Keep the gates separate:

1. Recover five further graphs. Validate order, edge count, α, triangle
   avoidance and criticality; prove mutual nonisomorphism independently
   (not merely distinct graph6), and check both partitions and complete
   union against GR Table 14 (32,108).
2. Bind each newly recovered key to exclusion of **degree-seven MTF
   extensions** by its actual demand clique or regenerated CNF/proof,
   including all earlier critical tranches in the ordered cover. B-027
   is semantically checked by the critic; H checks only the receipts.
3. Independently bind the same extension cover for every one of the
   2,102,271 reducibles, including every non-clique row. The 4,096
   dispersed pilot is 3,923 cliques + 173 pinned dual proofs, about
   2.3 CPU-h in the producer estimate, not a terminal verdict or total
   audit budget. Do not start production before census completion.
4. Only then can the independently reviewed exclusion be used for
   floor 109 via the prior lower floor 108. Apply any resulting exact
   distribution deltas separately. No change to U88.

Confirmed ledger remains at 278 near-regular MTF distributions plus R;
new narrow submissions are pending. The next cheap B action is the
545 not freshly bound set-aside parents if approved, not a general
e98 campaign. The best stronger regular-case evidence is D's necessary
111-root cover and C's now-audited reciprocal cut, neither a closure.
