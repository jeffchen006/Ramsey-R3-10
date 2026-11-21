# Lane F, round 3

## Before scale-up

The new move frees whole windows of vertex orbits, not just cross-star flips. The outside induced graph is pinned, but incident edge orbits, internal edge orbits, and outside degrees can change. The solver forbids triangles, enforces degree and edge bounds and the appropriate fixed-attachment bound, and separates independent-set constraints lazily. A bad set avoiding the window cannot be repaired and contributes to a fixed score floor. A bad set meeting the window gives a disjunction of mutable edge variables; asymmetric copies collapse as clauses in the zero-slack case. With positive slack, a failed orbit clause incurs its **size** in independent sets, not one unit. Extra distinct totalizer inputs are implied by the single penalty literal. Only a full independent-set recount below the bound can produce a checkpoint.

The n35 planted start (1,885 bad sets) reaches the gated C35 graph. On the matched n38 flexible start (50 bad sets) and the old fixed-interior finish (14), the move reaches gated n38 solutions. A deterministic compound perturbation of a valid involutory n38 graph gives 356 bad sets; zero two-orbit and 40 three-orbit transversals. First three-orbit solve reaches a gated n38 graph in 0.047 window CPU s. A separate small labelled test brute-forces edge-orbit assignments under mixed point-orbit sizes, triangles, degree, edge, attachment, flip and independent-set budgets; 300/300 match (240 positive slack). Initial `oracle` exposed `ITotalizer.extend` on an empty tree; fixed construction-on-first-cost and used distinct weighted inputs, then reran as `oracle2`. Only `oracle2` counts as a pass.

For the existing `(3,10)` anchor (I10=44, all degrees 9), complete window ranks give zero two-/three-orbit transversals, 175 four-orbit transversals. Exact sample at rank ranges 0–11, 60–71, and 120–131: 36 UNSAT, zero cap, 2.85 CPU s including startup. Remaining 139 windows cost an estimated 11.0 CPU s if representative, and at most the per-worker limits if the unmeasured tail is harder. Wide windows and score budgets are uncalibrated in cost on this target, so only bounded samples, no long launch. All `(3,10)` target runs restrict fixed attachment `a<=4` and degree 4..9, e>=161. A cap never implies exhaustion.

## Results (no candidate)

- **enum, one seed only:** no solution changes only edges incident with at most four vertex orbits of the *specified* order-three permutation, in the stated domain. A necessary condition is to pick a transversal of its existing independent 10-sets. Any smaller transversal can be padded to size four. Independent plain-Python enumeration rebuilt the 44 bad sets and checked exact equality of all 175 size-four transversals against the six completed job logs. All 175 returned UNSAT with no caps. Solver proofs were not saved. The replay checks coverage, not CDCL proofs. This differs from round 2's four-vertex test: the surviving orbit windows contain up to eight vertices and prescribe the order-three symmetry. It is not a closure of the family or of any degree distribution.
- **estimate:** seed the exact SAT instance with a cap of 12,000 valid independent-set clauses. Enumerate sets with few window vertices and a large independent subset of the frozen outside first; one representative for the window subset suffices when all of the available outside sets are included (capped subsets are only a strength reduction). On the same first 12 width-five windows, plain lazy returned 10 UNSAT/2 caps in 31.35 CPU s, frontier 12 UNSAT/0 caps in 6.83 CPU s (4.59x). Two dispersed 12-window frontier samples at indices 945 and 1850 returned 24/24 UNSAT in 3.12 + 3.49 CPU s including startup. Only 39 of 2,580 width-five windows were touched across all pilots. For the first 12 width-six windows, 3 UNSAT in 50.95 CPU s vs 4 UNSAT in 49.19 CPU s; there are 14,332 width-six transversals. Do not extrapolate a full classification from these samples.
- **open:** width-three strict-improvement sample `I10<=43` with at most 8 flips: 15/15 UNSAT. Width four with at most 16 flips: seven per-window caps, then CPU limit, no completed search. Width-three escape (`5..15` flips, `I10<=50`): 20 labelled models, all score 44 and in the anchor's ordinary isomorphism class (see `escape.classes`). Minimum edge-orbit edit distance does not ensure a different graph class. As a non-isomorphism test, try the same capped search with `e<=179`: the width-three sample returns 12 UNSAT for `I10<=65` within its 15-flip cap; width four reaches seven per-window caps then CPU limit. These are bounded queries, not entire neighborhoods.
- **open:** cumulative degree-valid target best remains I10=44 for `(3,10)`, e=180, degrees 9. Raw I10=30 still violates the degree cap. All other families carried forward without new exposure, in `round3_nearness.tsv`. No candidate was put in `ralph/found/`.

## Reproduction

All paths are workspace-relative unless in the `cd` block. The input anchor digest is `3980230c9f7f5527c166149c6614a8eb80e59e385b872a479526eaa502281dc0`. Full arguments, logs, start ticks and wall/CPU caps are in `STATE.md` and `scratch/F/{supervisors.tsv,concurrency.log}`.

```sh
export TMPDIR="$PWD/scratch/F/build"
g++ -std=c++17 -Wall -Wextra -O3 -march=native -shared -fPIC \
    ralph/lanes/F/window_sets.cpp -o scratch/F/build/window_sets.so
cd scratch/F/r3
python3 -B ../../../ralph/lanes/F/window_audit.py ../r1/long_p3f10.best.g6 \
    pilot40exact*.stdout rest40exact*.stdout
```

`window_control.py` with no arguments reruns the 300 labeled comparisons. With `--fixture ../r1/fast38_m2.found.g6 ctl38compound.input.g6`, it recreates the positive compound input. `ctl38comp.gate`, `ctl38front.gate`, `ctl38edge.gate`, `ctl35.0.0.gate`, `ctl38base.0.0.gate` and `ctl38flex.0.0.gate` record independent successful checks. A corrupt or absent log is not accepted by `window_audit.py` as full coverage. Near-positive checkpoints (score >0) are never passed off as candidates.
