# Lane G state — round 4, 2026-11-21

## Round 4: eight e168 cuts and strict residue census

| Label | Result | Evidence | CPU-h (approx.) |
|---|---|---|---:|
| hand + cert | Equality in the MTF private bound forces a simple signature graph on the six neighbours, with exactly six possible class profiles. Six e168 cuts have exact rational certificates using accepted floors 120/107 and published floors 95/86, independent of both gluing floors. Seven matched t9 improvements at the old threshold minus one, six overlapping the eight cuts. | `rows/equality_private.md`, `private_equality_{cuts,t9}.jsonl`, `scan_private_equality.py` | <0.05 |
| hand + cert | Two independent e168 cuts `(5,0,9,26)` and `(6,2,2,30)` use matching parity and typed pair packing, needing floor 120 only. Checked unit-weight Farkas sums give `0<=-1` and `0<=-2`. Separate exact packing enumerator agrees on all eight new cuts; 2,450 brute-matched small controls. | `rows/private_packing.md`, `check_private_packing_cuts.py`, `round4_cases.csv` | <0.001 |
| cert (individual) | All 1,223 strict e120 residues ruled out at a degree-six MTF root: 1,157 checked demand cliques, 66 dual-checked LRATs. No-solve replay passes. | `replay_e120_partial.sh`, `root_certs/e120_partial.sha256`, `scratch/G/round4/e120_replay.log` | 0.01 |
| cert (individual, total e<=169) | All 13,092 supplied e121 residues ruled out for an MTF degree-six root through total e169: 10,268 cliques and 2,813 core LRATs unpinned; 11 other LRATs pinned to total e169, the first possible total by Z>=48. Combined known catalogue is 14,389 of 14,395, so at most six as yet unidentified e120/e121 types can occur at degree-six roots through e169; no new global floor. | `scratch/G/round4/{e121.frozen.g6,e121.frozen.count.log,e121.frozen.sha256,e121.shards.replayed,e121_e169/proofs.log}`, `root_certs/e121_frozen.sha256` | ~0.15 |
| enum / open | Cached witness edits and up/down bridges reached the strict combined count 14,389 (e120=1,223, e121=13,092). All 12,289 e121 children of the known e120s are covered, and thinning every known e121 returns exactly the 1,223 known e120s. Exactly 803 supplied e121s are deletion-critical. At most six combined types remain; completeness is not inferred from any move. | `witness_edit.cc`, `scratch/G/round4/{e121.frozen.critical.g6,e121.critical.log,*.plan}`, `LOG.md` | ~1.3 |

**368 near-regular distributions + R remain**, conditional on the accepted
baseline and pending review of the eight additional cuts. **12** would be
cut by a complete MTF e88 exclusion. The 8 new cuts themselves do not need
gluing. There is no claim of floor 121 or 122 until the strict combined cover
is independently bound. `round3_frozen.csv` was delivered to H/A/B; A owns
independent catalogue packaging. No e107 scaling this round.

No detached jobs. The final optional supervisors below were stopped
explicitly after inspecting their PID arguments; their current children
were limited to 30/15 seconds. No inference from stopped probes.

| PID | Command / log | Cores | Start | Expected end |
|---:|---|---:|---|---|
| 2734616 | Foreground sequential unpinned full-CNF CaDiCaL, `scratch/G/round4/e121_full/proofs.log` | 1 | 20:45 | stopped 20:48 |
| 2742562 | Foreground sequential unpinned triple-column CaDiCaL, `scratch/G/round4/e121_pairs/proofs.log` | 1 | 20:47 | stopped 20:48 |

Next: seek exact remaining six via the
original archive or a targeted decomposition, not another unconditional
2-edit sweep; the matched e122 lateral closure and broad e123 return
added only two and one e121 classes respectively. A/H: independently
replay the equality and packing cuts, and bind the partial census. If
the six keys are obtained, filter by demand clique before LRAT. Do not
mistake the strict count or ordinary graph validity for extendability.

The e120 list in round 3 had 1,177 strict e120s plus one e119 (not 1,178
e120s). Likewise the 10,843 e121 frontier had 23 e120s. Their proof runs
were still valid for each supplied residue, and the accepted floor 120 /
floor 107 and e167 cuts use the separate clean catalogues. Round 4 uses
explicit level splits, independent alpha/triangle checks and canonical
distinctness (`check_floor121_catalogue.py`).

## Round 3 handoff (historical)

## Round 3 result and jobs

No detached jobs; all bounded runs finished. Peak nine enumerator/checker
workers (six backward e120 shards and three e106 exception shards), under the
allocation of 18; no job to pick up or kill.

| Label | Result | Evidence | CPU-h (approx.) |
|---|---|---|---:|
| enum | Tagged two-/three-vertex replacement found the missing six e119 residues; exact small controls 84/168 marked cores, plus all e118 marked originals. Complete by published counts, not by closure of the move. | `joint_replace.cc`, `check_joint_replace.py`, `root_certs/{new119,complete33_le119}.g6`, `LOG.md` | 0.05 |
| cert | All 74 e118/119 residues are valid and canonically distinct, both LRATs pass. MTF degree-six floor 120 at every total e, independent of gluing. Exact Farkas clears all 56 original e167 n6>0 distributions, 55 incremental. | `rows/floor120.md`, `root_certs/closed167.csv`, `replay_floor120.sh`, `scratch/G/round3/full_verify_floor120.log` | 0.006 |
| cert | New MTF degree-seven floor 107 at every total e, independent of gluing or the degree-six floor. GR counts 39/952/18598 at 104/105/106; 19521 independently checked demand cliques, 68 remaining both LRAT checkers. | `rows/floor7.md`, `verify_uncovered.py`, `root_certs/floor7_inputs.sha256`, `replay_floor7.sh`, `scratch/G/round3/floor7_replay.log` | 0.04 |
| cert (conditional) | Floor 120 improves 35/213 t9 bounds with 36 rational certificates; no incremental closure beyond e167. Degree-seven floors 105/106/107 improve 39/45/44 more t9 bounds (40/48/45 rational certificates); close 8/6/9 more distributions, respectively, conditional on e(H8)>=97 and e(H9)>=88. | `root_floor120_certs.jsonl`, `root_floor7{,_106,_107}_certs.jsonl`, `round3_cases.csv`, `scratch/G/round3/floor7.*.verify.log` | 0.07 |
| cert (individual) / open (cover) | 1178 valid nonisomorphic e120 order-33 residues; all individually ruled out (1125 cliques, 53 checked LRATs). True count lies 1223..1240 (GR lower bounds + Ang exact <=121 total); at least 45 still missing. No next degree-six floor or e168 closure. | `scratch/G/round3/{back120.union.g6,e120.catalogue.log,e120.cliq.log,e120_exception_core.log}` | 0.46 |
| enum / open | Order-32 e107: all immediate additions give 234341/234681; tagged 60-source pair pilot adds 11 unique classes; 329 missing. 2925/2967 sampled clique witnesses verified. No floor 108. | `scratch/G/round3/{e107.partial.g6,e107.survey.*,e107.pilot.cliq.tsv}` | 0.005 |

**78 incremental exclusions in round 3; 376 near-regular distributions + R
remain**, conditional on the prior gluing floors and subject to critic review.
The 55 e167 additions do not rely on gluing. Complete e88 MTF gluing would
now cut **13 more** (363+R remain); no such gluing conclusion is claimed.
`summarize_round3.py` reproduces `round3_cases.csv`, including all overlaps.

Next: independent review of `replay_floor120.sh` and `replay_floor7.sh` (no
solve). Use demand cliques for fixed-root prefilters. Close the e120 or e107
catalogue gap only with a new exact source/critical-edge decomposition; do
not relaunch the same measured seeded sweeps blindly. A full e120 exclusion
would directly settle 47 e168 n6>0 distributions on the floor-120 baseline
before overlaps with the new d7 LP cuts. Full e107 pair expansion alone has
an estimated ~0.9 CPU-h and ~6 GB raw stream; no commitment to coverage.

## Round 2 handoff (historical)

### Round 2 results

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
