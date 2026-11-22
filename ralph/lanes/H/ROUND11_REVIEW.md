# Lane H, round 11 — November 22, 2026

## Lean scope and replay

- `lean/R310/AnchorSaturation.lean` proves `|X|+4 ≤ 3α` for a
  triangle-free graph with exterior X covered by cross, side, other;
  cross and side are distinct nonadjacent vertices outside X, and the
  cross anchor has an extra neighbour outside X. Split the cross
  nonneighbours by adjacency to side. The first cell plus cross is
  independent; the second plus cross and side is independent. Thus
  `|off|+3 ≤ 2α`; at most `α−1` exterior vertices meet cross. This
  replaces singleton/double multiplicity premises, not the obligation
  to prove that the paired-window data wires up the marks and cover.
  The `α≤6` corollary gives `|X|≤14` and contradicts the 15-slot core.
- `noncross_anchor_order_le_degree_add_twenty_two` performs the
  closed-neighbourhood deletion: all seven other anchors survive,
  residual α≤6, and exterior cardinality is preserved under subtyping.
  It derives `order ≤ d(root)+22` directly, with no R(3,7) table.
  It does not formalize the 14-slot deficit type, the actual mixed
  leaf/cross minimum geometry, catalogue completeness, or pivot swap.
- `lean/R310/IntersectingPairs.lean` proves D's set classification
  including empty family, common hub, or exactly three edges on three
  distinct vertices. In the no-hub branch two incident edges are
  forced, then the edge avoiding the intersection must be the third
  triangle edge. It does not establish either solver exhaustion in
  D-020, the R(3) conclusion itself or the four-star rooted cover.

With the existing pinned cache (no Mathlib source build):

```bash
bash ralph/lanes/H/build_private_signature.sh build --old R310
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 ../ralph/lanes/H/AxiomsRound11.lean
bash ralph/lanes/H/build_private_signature.sh env lean -j1 -s8192 scripts/Axioms.lean
python3 -SB ralph/lanes/H/check_axioms.py ralph/lanes/H/AxiomsRound11.lean scratch/H/round11-targeted.log
python3 -SB ralph/lanes/H/check_axioms.py lean/scripts/Axioms.lean scratch/H/round11-project.log
python3 -SB ralph/lanes/H/check_round11_controls.py
python3 -SB ralph/lanes/H/check_round11_receipts.py
```

Build success, six targeted and 306 integrated axiom reports; only
`propext`, `Classical.choice`, `Quot.sound`. Checker logs:
`scratch/H/round11-{build-final,targeted,project,controls,receipts}.log`.
The known McKay `r35_13.g6`/`r36_17.g6`/`r37_22.g6` inputs (1/7/191)
are saved at `scratch/H/lit/r11-*`. Independent graph6/alpha checks
and marked tests give 936/22,474/1,894,780 controls, observed maxima
7/11/14 vs bounds 8/11/14. In the latter two lists there are 60/6,984
tight exterior marks, each violating the bound if the extra neighbour
is restored to X. The first test incorrectly expected tightness on
order 13; it found 7, which satisfies the inequality. The pair check
enumerates all families on at most six vertices; on six: 1 empty,
171 hub, 20 exact triangle, 32,576 with a disjoint pair. These are
controls for interfaces, not a replay of G/D's case exclusions.

## Claim and evidence hygiene

- Imported round-010 critic verdicts. No distribution arithmetic.
  D-020/021 are a necessary matching with hand+enum and separate
  78 local certs. G-034/035 are minima only; G-037 remains pending
  round-11 audit with independent source identities separate from
  pin/proof binding. F-013 threshold is not the F-014 LRAT conclusion.
- B round-011 provenance: recomputed exact sorted disjoint merge of
  old union plus 47 new graph6 keys (1,875 critical, 2,104,146 total).
  The 37 clique indices and 10 residual IDs cover the entire tranche;
  residual graph6 and production/replay digest pairs match, as do
  the ten stored proof digests. H neither verifies clique semantics
  nor regenerates proof CNFs nor replays a kernel in this check.
  Five absent remains an open census under review. Not floor 109.
- Follow up next round on the 7,954 untested e98 parent queue and the
  cap-five reciprocal 22/21 verification. Distinguish e168 direct
  addback shells from exclusion proofs and order-21 measured singleton
  deficit from a hand conclusion about all weak marks.
