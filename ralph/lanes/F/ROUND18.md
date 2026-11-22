# Round 18: two reusable column cuts in one calculation

**Result (hand + enum, pending critic review):** of the 7,448 previously unresolved no-double footprints on the 17 untouched sites, **7,184 are impossible and 264 remain open**. Each cut applies both to an arbitrary exterior pole and to one endpoint of the exceptional site. Repricing the same marked relaxation, not enumerating its pairs, reduces **353,474,849 to 16,182,483 unsigned joint headers**. No signing or graph realization was sought or inferred. No unrestricted Ramsey case is closed.

## What is tested

The premises and prior cuts are exactly `ROUND17.md`: sites 1..17 have single inter-pair matchings at absolute differences 6..12 and no other inter-pair edges. The internal edge of each pair is arbitrary. A no-double pole meets at most one endpoint of each site. Bit 0 in a support mask denotes physical site 1, not the exceptional site 0. Reversing these 17 bits fixes the exceptional site. The target is triangle-free with no independent ten. The cuts use only the 34 untouched vertices and at most one additional vertex. When that vertex is the first marked endpoint, its mate and all four exterior vertices are irrelevant. This explains reuse without identifying independent endpoint orientations once the two columns are joined.

Interchange endpoints at every contacted site as necessary to name the pole's neighbor bit 0. For a quotient edge `ij`, let `s_ij` be the XOR of bits at **nonmatched** ends, so an independent singleton transversal on support `T` is a solution of `x_i + x_j = s_ij` for its induced edges. Triangle-freeness sets the sum of the three `s` on each quotient triangle to 0, since the three physical matching parities are the complements of `s`. It sets `s_ij=0` on every edge joining two contacted sites. For a nine-support with the pole, also set `x_i=1` on contacted selected sites; for a ten-support without the pole there are no pins. No transversal tests a vertical, nor do we add verticals in the physical graph.

Each receipt is a sequence of support masks and claimed affine forms in the **original matching coordinates** (the low bit is the constant). Eliminate the temporary `x_i` from the support equations. If every residual vanishes modulo prior constraints the independent ten is forced. If the nonzero residuals all agree modulo prior constraints, their common form must be one, or an independent ten exists. Other ranks produce no deduction. The C++ searcher uses component paths; the Python checker builds the equations above instead, checks the projected forms one by one, and rejects out-of-bank supports, invalid ranks or inconsistent trace endings. A terminal `open` certifies nothing. The result is `enum`, not LRAT/Lean.

## Fixed banks, controls and independent checks

- Initial bank: extract 125 distinct step supports from round 17 `pilot0.trace`, take all translates and reflections contained in the linear 17-site interval. These 237 nine- and 34 ten-supports were frozen before their 128-footprint price pilot. Translating the *support* is allowed because every deduction is rederived at its actual coordinates; no cyclic group or unmarked dihedral symmetry is assumed. Pilot: 123 forced contradictions, five open. Full: **7,056/7,448** contradictions, 139,198 verified deduction steps (including open traces). Intermediate header price **18,426,195**.
- Deterministic extension only for those same 392 still-open footprints: all 24,310 nine- and 19,448 ten-supports, eight rank-one passes maximum. Pilot: 8/32 cut. Complete: **128 further cuts**, 5,763 checked deduction steps. No quadratic probe, signing split or other footprint was run. The exact inventories are `scratch/F/r18/{frozen,wider}.bank`; forecasts and bank hashes precede production in `forecast.txt`, `prep.stdout` and `extend.stdout` there.
- Marked physical control: the 7-vertex puncture of `C8(1,4)` with sites `[(0,4),(1,5),(2,6)]` and pole `3` is triangle-free with no I4 (gate and direct enumeration). Its footprint `{0,2}` stays open. Isolate the pole: the gate and literal I4 mask 89 reject; the bank finds a forced I4. The independent verifier rejects a deliberately forged contradiction on the positive footprint. Evidence: `ctlprep.stdout`, `small.trace`, `ctlcheck.stdout`, `tamper.stdout`.
- Reconciliation: 12,020 prior no-double reps, 4,558 prior prism cuts, 33 prior pilot cuts with 19 overlapping prisms. Thus exactly 7,448 new-domain reps; all 7,184 new cuts disjoint from both old sets. Under the one physical reversal the new cuts represent **14,296 labelled masks, 72 fixed**. The 264 open pole reps represent **512 labels, 16 fixed**. All cut masks appear in the altered-marker domain as well. The unchanged cyclic row is omitted as before; it is not one of these cuts.

## Arithmetic price (not a completion count)

| Marginal after new cuts | Representatives | Physical labels | Reversal-fixed | Reps by number of double hits |
|---|---:|---:|---:|---|
| Altered marked row | 1,327 | 2,622 | 32 | 263 / 1,050 / 14 |
| Arbitrary first exterior pole | 4,411 | 8,779 | 43 | 264 / 3,709 / 412 / 26 |

| Pole contacts at marker | Labelled joint headers | Fixed under simultaneous reversal | Joint orbits |
|---:|---:|---:|---:|
| 0 | 23,018,538 | 1,376 | 11,509,957 |
| 1 | 8,117,807 | 529 | 4,059,168 |
| 2 | 1,226,645 | 71 | 613,358 |

Forward and reverse bitset counts agree using the frozen round-17 feasibility masks. They take half of labelled plus *simultaneously* fixed counts, not independent quotients for the two columns. The 12 cells by number of full sites in each role add back to each of the three joint-orbit totals; `scratch/F/r18/{stratprice.stdout,doubleprice.tsv,widemark.left,widepole.left}`. Of the 16,182,483 remaining, **15,573,942 have exactly one double in at least one role**. This is the size of a potential filter's domain of influence, not an estimate of its exclusions.

## Handoff

Clean rebuild: from a new empty `scratch/F/` subdirectory run `bash ../../../ralph/lanes/F/round18_replay.sh`. The replay rebuilt both stages, rechecked every deduction and byte-compared banks, physical controls, rosters, traces, cut lists, marginals and the stratified price. `scratch/F/r18/{jobs.tsv,clean.stdout,*.time}`, `ROUND18_FREEZE.sha256`. Measured total **15.13 CPU-s = 0.00420 core-h** including clean replay and pricing; peak 167,936 KiB RSS, one worker maximum. No candidate or running job. Empirical best unchanged: 24 independent tens at 178 and 179 edges; `round18_nearness.tsv`.

**Stop here.** Do not scan the 16 million joint headers or spend more on the 264 rank-open single columns without a new idea. If authorized, the next cheap test is to group **3,709 exactly-one-double exterior footprints** by the doubled site's label, restoring that site as two auxiliary columns as in round 17. Price one frozen bank per removed site with physical pole-to-double edges and complementary pins checked, first on the marked positive/adverse controls and a dispersed pilot. The 1,050 marked rows in that stratum reuse the cuts when applicable. No additional cores requested; no rate is inferred for this untested population.
