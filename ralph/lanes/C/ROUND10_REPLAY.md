# Round 10 — bounded reciprocal 22/21 join (November 22, 2026)

**No candidate and no case closure.** The new 22/21 result is a finite
sample, not a complete source. The reproduced cap-five 22/22 exclusion
is only for that marked profile, not an exclusion of R(5). Nothing is
claimed here about the cap-six or 21/21 joins. `S/` below is
`scratch/C/r10/`. Replay with `bash ralph/lanes/C/replay_reciprocal_r10.sh`;
the pre-run limits are in `ROUND10_PLAN.md`, and the formalizable
degree/cover argument is in `proofs/reciprocal_windows.md`.

## Controls and equal join — hand + enum

- Independently decoded the ten 6-regular order-22 control graphs and
  extracted all 395 exact 10/11 planted marks, with 40,40,40,44,40,40,
  48,33,35,35 respectively. All appeared as `live` in the marked
  same-parent indexed runs. On six left and six right control windows,
  the index, the no-index C++ join, and Python enumerating all core
  permutations give **exactly the same 4,882 keys**, not just the same
  counts. The no-index join tests 21,280 card pairs. `S/cal-check.log`.
- The order-22 source gives 191 pairwise nonisomorphic graphs by
  `shortg`; direct triangle and independent-seven checks pass on all
  191 (and the 8,192 sampled order-21 hosts). Completeness of the
  191 classes follows using [D-C7], not just a match of file lengths.
- Reproduced the scout's exhaustive cap-five 22/22 join:
  **278,160 marks, 202,980 cards, 13,875 request keys, zero key matches**.
  The separate full order-22 side of 22/21 has 7,791,069 marks,
  2,883,465 cards and 12,482 request keys; card IDs and multiplicities
  match the scout byte-for-byte (`cmp S/fixed22.tsv scratch/ideas/r009_R/wide22.tsv`).

## Held-out stream — enum

The seeded sampler draws 2,048 hosts per source-row quartile, excluding
both the earlier scout residue class modulo 4096 and its 1,024 random
IDs. Both IDs and raw graph strings are disjoint from the scout pilots.
Canonicalization of the combined 9,490 graphs also shows they are all
nonisomorphic (`S/sample-shortg.log`). The stream keeps only the current
right host and retains only cards whose keys hit a fixed-index bucket;
it does not materialize a right-side census. Journal keys are
`lhs row core mask0 mask1 mask2 rhs sample-row core mask0 mask1 mask2`
followed by the ordered images of the core, reason and witness. Convert
the right sample row to a catalogue row using `pilot-ids.tsv`.

| Quartile | Order-21 hosts | Exact role maps | Undecided | Stream CPU-s after index |
|---|---:|---:|---:|---:|
| 1 | 2,048 | 9,062 | 0 | 1.46 |
| 2 | 2,048 | 14,193 | 0 | 1.40 |
| 3 | 2,048 | 43,781 | 0 | 2.22 |
| 4 | 2,048 | 3,193 | 0 | 1.69 |
| Total | 8,192 | 70,229 | **0** | 6.78 |

The first index build took 8.95 CPU-s; `/usr/bin/time` reports
**16.46 CPU-s end-to-end**, 22.23 elapsed seconds, under 400 MiB max RSS.
There were 34,172 candidate card pairs, 57,121 weighted mark pairs,
and 41,907 aligned card maps. Exactly 55,563 maps have a direct
independent-ten witness in the upper graph, 8,532 a fixed undominated
pair, 5,355 an already spent codegree cap and **779** require row/domain
propagation (439 domain-IS, 173 row-column, 118 forced-domain, 49 row-empty).

**Independent replay:** materialize only the pilot's alternate scout
right card source and use its separate index and Python mark generator.
The scout counts 67 additional raw local marks because its fast source
only checks equality to the cap/near-cap at single and double marks,
whereas the stream checks greater-than-or-equal; no additional
matched card or mark is affected. Per-card regeneration agrees on all
15,540 matched card multiplicities. An independently coded aligner
reconstructs the **entire set of 70,229 exact keys**. It independently
verifies all 69,450 direct witnesses, and replays an alternative
domain propagation on all 779 other maps with zero survivors. CPU:
16.62 s alternate source/index and 43.92 s independent replay.
`S/scout-{index,right}.log`, `S/audit.log`. The raw 67 discrepancy is
outside the queried index and is not a disagreement of exact keys.

## Bound proof-cost sample — cert (48 maps only)

Choose eight keys per non-cap outcome, with fixed seed and receipt
bindings. Four planted asymmetric controls give independently checked
SAT models. Two checkers verify all 48 dense and all 48 thin target
LRATs. On an initial empty input axiom, the binder writes a one-line RUP
copy citing that axiom rather than treating an empty/partial solver
trace as verified. The thin pass preserves the same degree and triangle
clauses and selects only a subset of valid independent-set clauses, by
solving relaxed models and blocking independent sets they contain;
the final CNF is solved/checked separately. `proof-compare.log` confirms
each thin target clause belongs to its original dense formula and all
48 keys and hashes agree. No target completion is pinned or assumed.

| Variant | Generation CPU-s | Solver CPU-s | Dual checking CPU-s | Whole process CPU-s |
|---|---:|---:|---:|---:|
| Dense | 20.89 | 0.91 | 6.14 | 29.63 |
| Thin | 1.11 | 1.35 | 3.52 | 7.54 |

This is **3.93×** on the same proof keys, not a general SAT speedup.
The thin `forced-domain` category is the expensive tail (0.380 CPU-s
per sampled map excluding process overhead vs 0.065–0.085 for each
other category). Use direct witnesses for the elementary three
categories, and price the 779-map stage, not a full proof for each
aligned map. `S/proof-{control,pilot}{,-thin}/receipts.tsv`.

## Prospective cost — estimate, not authorization

At the measured average density ~9.59 million aligned role maps
would be checked over 1,118,436 hosts, with ~106,350 domain cases and
roughly 1 GiB of stream journal. Reusing one index gives ~0.26 CPU-h
for the fast stream (0.34 at the slowest quartile rate). Straight
extrapolation of the slower independent replay and alternate pilot
build is ~2.3 CPU-h, preferably in shards to avoid a multi-GiB mark
intermediate. Weighting per-class proof measurements by the observed
domain case frequencies gives ~3.8 CPU-h plus ~1 CPU-h of measured
process overhead using thin proofs, versus ~18 CPU-h for dense proof
production alone. A 7–16 CPU-h planning range for fast stream plus
exact audit plus thin proof queue is plausible based on average and
busy-quartile densities, **excluding full catalogue provenance checks**;
it is not an upper bound. Do not run the census this round. The
diagonal-four 47/24 split is unchanged and all round-9 hashes pass.
