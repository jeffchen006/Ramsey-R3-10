# Lane G state — round 1, 2026-11-21

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

## Next

Ask critic/H to re-check the six certificates and B to apply the updated
threshold table. If B's t9<=88 gluing succeeds, it removes **24 more** after
the six above (not 30 more), leaving 494 + R. Do not treat this as done.
The pair/edge-table aggregate rows add no closures in this relaxation; the
productive new restriction was the type-6/7 wedge budget with vertex-level
rounding. Next candidate: try exact rooted degree/mask feasibility (especially
degree 6) or certified integer branching on a sample of the lowest-e survivors;
avoid spending cores on an undifferentiated stronger pair LP.
