# Round 7: degree-preserving vertical trades

No candidate and no improvement on the degree-valid best I10=24. All
target claims are about two fixed labelled neighborhoods, not an
exclusion of the free-involution family.

## Move (hand)

Use the round-6 quotient of a free involution. Its diagonal bit records a
vertical edge; an off-diagonal weight is the number of matching orbits.
The row sum, counting the diagonal once, is each fiber vertex's degree.
For a simple path of distinct fibers, change its off-diagonal weights by
one unit with alternating signs and toggle the vertical bits at both
endpoints. Choose the first off-diagonal sign to cancel the first bit
change and require the last off-diagonal sign to cancel the last bit
change. All interior row sums cancel as well, so both the degree vector
and the physical edge count are unchanged. We enumerate every such path
of length 1 through 4 by DFS with the smaller endpoint first, rejecting
out-of-range weights. The final triangle-feasibility filter is precisely
the double-edge check from `ROUND6.md` (all single matchings crossed give
a lift whenever that check passes). Each move reverses by the same path
with all signs reversed. Ordinary off-diagonal two-switches never change
vertical bits, so cannot recover the marked original after this edit.

## Calibration and result

Logs below are relative to `scratch/F/r7/`.

| Label | Scope and result | Evidence |
|---|---|---|
| enum | 64 random legal small quotients: exact output sets agree with the direct changed-cell subset/sign oracle plus an explicit all-crossed triangle check. 84/74/69/28 generated outputs across lengths 1/2/3/4. | `generator_oracle.stdout`, `ralph/lanes/F/vertical_trade.py` |
| enum | On two known n38 graphs, sample one mutant per length, without selecting on score. For the same eight mutants, exact relift at zero succeeds in 8/8 reverse trade neighborhoods, 0/8 complete ordinary two-switch neighborhoods, and 0/8 mutants. 6,843 row decisions, no caps. The two distinct recovered labelled graphs pass the 38,10 gate. This is a planted recovery comparison, not a natural target hit-rate estimate. | `prepare_ctl.stdout`, `calibration{0,1}.stdout`, `ctl[01]_[1-4].{q,expected,log,tsv}`, `ctl{0,1}.gate` |
| estimate / enum | 218 target pilot rows, both ceilings 23 and 80, cost 20.06 CPU-s. Three ceiling-80 witnesses recount to 60, 24 and 74; zero at ceiling 23. The score-24 witness is a seed copy. Uniform scaling at both ceilings would cost about 386 CPU-s; we instead ran the full tier at 24 (14.17 CPU-s including audits). | `target_pilot.{stdout,time}`, `target_cost.txt`, `target_full{0,1}.time` |
| enum | Complete legal length-1–4 neighborhoods of the e178 and e179 score-24 seeds: respectively 2,258 and 1,938 rows, distinct labelled rows and disjoint from the round-6 inputs. At ceiling 24, 4,194 no and two yes, both from length 2. Both yes rows exhaust at 23, so neither has a better signing. The two **emitted** score-24 lifts are each isomorphic to their own seed (not a census of all ties). No filters or caps. | `prepare_target.stdout`, `target_full{0,1}.stdout`, `target[01]_[1-4]_24.{log,tsv}`, `close_audit.stdout`, `tie[01].log`, `round7.sha256` |

The nine registered jobs total 57.65 CPU-s (0.0160 core-hours), peak
two slots; all exit zero and none remain. `round7.sha256` also binds the
round-6 order-38 representatives in `../r6/sparse.distinct.g6`; nothing in
that pool or the round-6 input files was changed. Do not repeat these
neighborhoods or spend more cores composing the same trades without a
genuinely different source. No request for more cores.
