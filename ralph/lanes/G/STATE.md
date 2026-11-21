# Lane G state — round 2, 2026-11-21

## Round 2 results and live jobs

No detached jobs. All bounded runs used one core each; none remain at handoff.

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand + cert | In an MTF `(3,10,40)` graph every degree-six root leaves `e(H6)>=119`. Uses the complete GR Tables 4/14 `e=118` cover, not the degree-eight or degree-nine gluing floors. Both `lrat-check` and CakeLPR verified all five; 294 actual rooted controls satisfy every clause. | `rows/root_residue.md`, `root_certs/`, `replay_root_core.sh`, `scratch/G/root/{core_control,replay_core118,cover166}.log` | 0.001 |
| cert | Therefore `n6=0` at `e=166` (MTF gives `Z(v)>=48`); exact two-row Farkas refutations for all 65 distributions in original 524, including two previously closed. **63 incremental cuts**, independently of the gluing floors. | `root_certs/closed166.csv`, `check_root_distribution.py`, `rows/root_residue.md` | <0.001 |
| cert (individual roots), open (cover) | Regenerated 63 of 69 `e(H6)=119` classes. Both checkers exclude all 68 known residuals with `e(H6)<=119` regardless of total edges. **Six classes missing**; no `e(G)=167` stratum closure. | `root_certs/partial33_le119.g6`, `scratch/G/root/{catalogue119,replay_core119_clean}.log`, `LOG.md` | 0.023 including census probes |
| cert | The higher-e floor 119 tightened 61/269 t9 bounds in the remaining degree-six strata with `e>=167`; 63 exact Farkas certificates verified. At `e=167`, `(8,0,2,30)` lowers from 88 to 87, **one further closure conditional on the existing degree-8/9 gluing floors**. Five other distributions now have `t9<=88` (previously 89 or 90). | `root_floor_certs.jsonl`, `scan_root_floor.py`, `scratch/G/root/{floor_full,floor_verify}.log` | 0.031 |

**64 incremental exclusions this round; 454 near-regular distributions remain
plus Case R**, taking the prior gluing floors as given.

Requests: H/critic please supersede pending G-004 with the edge-count-free
five-input proof and the distribution consequence. B was told the exact scope:
of the 24 previously additional `t9=88` distributions, 8 overlap the e166
cuts and one the new e167 cut. Five more were newly lowered to 88:
`(4,7,0,29)`, `(6,2,0,32)`, `(6,4,0,30)`, `(7,0,1,32)`, `(7,1,1,31)`.
Hence an eventual e88 gluing closure would remove **20 more** now, leaving
434 near-regular + Case R. The six round-1 closures are individually listed below.

Next: prioritize finding or covering six missing order-33, e119 classes.
The complete cover with all individual certificates would raise the new
floor to 120 and close the 55 currently open e167 distributions with `n6>0`.
Simple edge additions, exact rewires, swaps and thinning have documented
diminishing returns (`LOG.md`); do not infer completeness or repeat them
without a new source of graph seeds. The fast essential CNF should be used
first on other fixed residuals, before listing any independent-set cuts.

## Round 1 handoff (previous results)

## Results and claims

All closures below concern the MTF near-regular list only. `R` is untouched.
The 524 denominator already excludes the 20 distributions from the original
two gluing runs. New LP claims are `cert` **conditional on** the stated
gluing floors; the underlying gluing results remain `enum`.

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| cert | Exact replication: 545 survivors, all four pinned t9 columns and 2,176 Farkas certificates byte-identical; 0 failures on exact recheck | `scratch/G/bootstrap/{baseline,verify}.log`; JSON compared to `lean/data/cases_pin1` | 0.018 |
| hand | Profile, degree-typed wedge, private, internal e(3,8), pair/P3, lifted and packing rows | `rows/*.md`, `typed_lp.py` | — |
| enum | Calibrated by substituting actual integer coordinates for C35, Exoo39, its MTF saturation, and all 191 repo (3,7,22) graphs; exact empty-row contradiction on (3,9,36) | `check_rows.py`, `scratch/G/check_rows.log` | <0.001 |
| cert | Six further distributions excluded given both original gluing floors `e(H_8)>=97`, `e(H_9)>=88`; 518 nonregular remain (+ R) | `close87.jsonl`, `scratch/G/{full87,verify87}.log` | 0.014 |
| cert | 231/524 certified improved t9 upper bounds given `e(H_8)>=97`; 30 of original 524 now have t9<=88 (was 15), including six already reduced to <=87 | `t9_round1.csv`, `t9_round1_certs.jsonl`, `scratch/G/summarize.log` | 0.086 |

Six excluded `(n6,n7,n8,n9)` vectors: `(0,16,4,20)`, `(0,17,2,21)`,
`(0,18,0,22)` at e=162; `(8,2,0,30)`, `(9,0,1,30)` at e=166;
`(8,0,0,32)` at e=168. The last has a short counting proof; see `rows/examples.md`.

| LP family | Closures of 524 at the existing floors | Better by >=1 at old t9 minus one |
|---|---:|---:|
| profiles | 3 | 90 |
| + typed wedges and codegree caps | 6 | 226 |
| wedges + private | 6 | 231 |
| wedges + internal edge-table average | 6 | 226 |
| wedges + pair bounds, typed C, class P3 | 6 | 226 |
| all preceding | 6 | 231 |
| wedges + lifted | 6 | not scanned at old t9 minus one |
| all preceding + lifted | 6 | 231 (bisection established some multi-edge improvements) |
| all preceding + lifted + packing | 6 | not scanned at old t9 minus one |

Lifted and packing threshold-87 ablations used 0.056 CPU-h combined;
`scratch/G/full_pack87.{log,jsonl}`. Among the 231 threshold improvements,
22 improve by at least two edges. The preliminary separate no-gluing
ablation reached its wall limit without a report; no inference from it.

Potential gluing coverage, measured on the original 524, cumulative:

| U9 | Pinned | New | Total nonregular open if gluing succeeds |
|---|---:|---:|---:|
| 87 | 0 | 6 | 518 |
| 88 | 15 | 30 | 494 |
| 89 | 39 | 68 | 456 |
| 90 | 82 | 120 | 404 |
| 91 | 141 | 186 | 338 |
| 92 | 221 | 261 | 263 |

## Jobs and reproducibility

No detached jobs launched. Foreground runs all use 1 core and explicit
wall/CPU/address-space limits. `REPRO.md` has commands; the successful
run used system SciPy 1.15.3 as the shared venv was being built. Data and
raw logs are under `scratch/G/`. The compact positive certificates are in
this lane, and `scan.py --verify --output FILE` exactly checks them without
importing SciPy. A `python3 -S` recheck passed all 231 threshold, 12 lifted/
packing, and 2,176 baseline certificates (`scratch/G/verify_pure.log`).
Table entries are upper bounds, not claims of optimality.

## Round 1 next steps (historical)

Ask critic/H to re-check the six certificates and B to apply the updated
threshold table. If B's t9<=88 gluing succeeds, it removes **24 more** after
the six above (not 30 more), leaving 494 + R. Do not treat this as done.
The pair/edge-table aggregate rows add no closures in this relaxation; the
productive new restriction was the type-6/7 wedge budget with vertex-level
rounding. Next candidate: try exact rooted degree/mask feasibility (especially
degree 6) or certified integer branching on a sample of the lowest-e survivors;
avoid spending cores on an undifferentiated stronger pair LP.
